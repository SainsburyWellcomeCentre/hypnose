# hypnose

## Installation
To set up a Bonsai environment to run a sequence, use a terminal to clone the hypnose repo into a local folder:

```
git clone https://github.com/SainsburyWellcomeCentre/hypnose.git
```

Now navigate into `hypnose/.bonsai` and run the `Setup.ps1` script (on Windows right-click >> Run with powershell). Once all dependencies have been restored Bonsai can be launched in a local environment from the `.exe` in this folder. Workflows can be found in the `src` folder.

## SequenceSandbox
The SequenceSandbox.bonsai workflow provides a sandbox for testing behavioral session types (e.g. singles, doubles, free-run). The Bonsai workflow itself has two parameters. One is an an initiation key (the keyboard input that will initiate the session) and the other is a .yml session settings file. This .yml file defines the experiment metadata, the named commands that can be sent to the olfactometer, and the command sequences that are presented during the experiment.

