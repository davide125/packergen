# PackerGen sample config
# - set the QEMU builder to use a modern EFI-enabled Virtio machine
# - install the evaluation version of Windows Server 2016 Core 
# - bootstrap chocolatey, install Win32-OpenSSH and use it to communicate with packer

config['preparers'] = [
  ISO(
    source='http://care.dlservice.microsoft.com/dl/download/1/6/F/16FA20E6-4662-482A-920B-1A45CF5AAE3C/14393.0.160715-1616.RS1_RELEASE_SERVER_EVAL_X64FRE_EN-US.ISO',
    checksum='e634269ef78f1181859f88708c6d03c12a250f4b66d8cbd3de2e3c18da1f96ff',
  ),
  VirtioWinDrivers(
    os='Win2016',
  ),
  WindowsAnswerFile(
    params={
      'driver_paths': ['A:\\'],
      'image_name': 'Windows Server 2016 SERVERSTANDARDCORE',
      'first_logon_commands': [
        # install chololatey and win32-openssh
        "powershell iex ((new-object net.webclient).DownloadString('https://raw.githubusercontent.com/DarwinJS/ChocoPackages/master/openssh/InstallChoco_and_win32-openssh_with_server.ps1'))",
      ],
      'users': {
        'Administrator': {
          'password': 'packer',
        },
      },
    },
  ),
]

config['packer'] = {
  "builders": [
    {
      "type": "qemu",
      "format": "qcow2",
      "communicator": "ssh",
      "accelerator": "kvm",
      "headless": "true",
      "boot_command": "a",
      "boot_wait": "1s",
      "ssh_username": "Administrator",
      "ssh_password": "packer",
      "ssh_timeout": "120m", 
      "disk_size": 51200,
      "disk_interface": "virtio",
      "net_device": "virtio-net",
      "machine_type": "q35",
      "qemuargs": [
        [ "-bios", "/usr/share/OVMF/OVMF_CODE.fd" ],
        [ "-m", "4096M" ],
        [ "-cpu", "host"],
        [ "-smp", "2,cores=2"]
      ]
    }
  ],
}
