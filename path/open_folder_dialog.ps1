Add-Type -AssemblyName System.windows.forms | Out-Null;

# enable visual styles will render the dialog with modern style
[System.Windows.Forms.Application]::EnableVisualStyles();
$dialog=New-Object System.Windows.Forms.FolderBrowserDialog;
$dialog.Description="Select Rainmeter Skins folder usually found in 'My Documents\Rainmeter\Skins'";
$dialog.ShowNewFolderButton=$false;
$dialog.ShowDialog() | Out-Null;

$folderName=$dialog.SelectedPath

if ([string]::IsNullOrEmpty($folderName)) {
    -1
}
else {
    $folderName
}