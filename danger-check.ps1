# Claude Code Dangerous Operation Detection Hook Script
# Prevents potentially destructive system operations

param(
    [Parameter(ValueFromPipeline=$true)]
    [string]$InputText
)

# Define dangerous operation patterns
$dangerPatterns = @(
    # Linux/Unix dangerous commands
    "rm\s+-[rf]+\s+/",
    "rm\s+-[rf]+\s+/\*",
    "rm\s+-rf\s+/",
    "rm\s+-rf\s+/\*",
    "dd\s+if=/dev/zero",
    "dd\s+if=/dev/random",
    "mkfs\.",          # Format filesystem
    ":\(\)\{\:\|\:\&\}\;:", # Fork bomb

    # Windows dangerous commands
    "format\s+[c-z]:",
    "del\s+/[sq]\s+[c-z]:\\",
    "rmdir\s+/s\s+[c-z]:\\",
    "rd\s+/s\s+[c-z]:\\",
    "diskpart",
    "clean\s+\w+",     # diskpart clean command

    # System destructive operations
    "shutdown.*(/s|/r|/p)",
    "init\s+0",
    "halt",
    "poweroff",
    "reboot\s+-f",
    "systemctl.*poweroff",
    "systemctl.*reboot",

    # Bootloader destruction
    "dd.*of=/dev/sda",
    "dd.*of=/dev/nvme",
    "grub-install.*--force"
)

# Test if input contains dangerous patterns
function Test-DangerousOperation {
    param([string]$text)

    if ([string]::IsNullOrEmpty($text)) {
        return $false
    }

    foreach ($pattern in $dangerPatterns) {
        if ($text -imatch $pattern) {
            return @{
                IsDangerous = $true
                MatchedPattern = $pattern
                Reason = "Dangerous operation detected: $pattern"
            }
        }
    }

    return $false
}

# Main logic: read from stdin
$reader = [Console]::In
$inputContent = $reader.ReadToEnd()

# Detect dangerous operations
$result = Test-DangerousOperation -text $inputContent

if ($result.IsDangerous) {
    # Output error to stderr
    $Host.UI.WriteErrorLine("=" * 60)
    $Host.UI.WriteErrorLine("  HOOK WARNING: Potentially dangerous operation detected!")
    $Host.UI.WriteErrorLine("=" * 60)
    $Host.UI.WriteErrorLine($result.Reason)
    $Host.UI.WriteErrorLine("")
    $Host.UI.WriteErrorLine("This operation has been blocked to protect your system.")
    $Host.UI.WriteErrorLine("If you really need to execute this operation:")
    $Host.UI.WriteErrorLine("1. Temporarily disable the hooks configuration")
    $Host.UI.WriteErrorLine("2. Or run the command directly in your terminal")
    $Host.UI.WriteErrorLine("=" * 60)

    # Return non-zero exit code to block operation
    exit 1
}

# Safe operation, return success
exit 0
