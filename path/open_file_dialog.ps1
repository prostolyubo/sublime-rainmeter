Add-Type -AssemblyName System.windows.forms | Out-Null;

# enable visual styles will render the dialog with modern style
[System.Windows.Forms.Application]::EnableVisualStyles();
$dialog=New-Object System.Windows.Forms.OpenFileDialog;
$dialog.Filter='Rainmeter Executable (Rainmeter.exe)|Rainmeter.exe|All files (*.*)|*.*';
$dialog.showHelp=$true;
$dialog.Title="Select location of Rainmeter.exe";
$dialog.ShowDialog() | Out-Null;

$fileName=$dialog.FileName

if ([string]::IsNullOrEmpty($fileName)) {
    return -1
}
else {
    return $fileName
}