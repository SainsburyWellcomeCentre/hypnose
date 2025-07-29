# hypnose

## Prerequisites

The following should be installed on a fresh system in order to bootstrap the Bonsai environment correctly:

* Windows 10 or greater
 * [Visual Studio Code](https://code.visualstudio.com/) (recommended for editing code scripts and git commits)
 * [.NET 8.0 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
 * [.NET Framework 4.7.2 Developer Pack](https://dotnet.microsoft.com/download/dotnet-framework/thank-you/net472-developer-pack-offline-installer) (required for intellisense when editing code scripts)
 * [Git for Windows](https://gitforwindows.org/) (recommended for cloning and manipulating this repository)
 * [Visual C++ Redistributable for Visual Studio 2012](https://www.microsoft.com/en-us/download/details.aspx?id=30679) (native dependency for OpenCV)
 * [FTDI D2XX COM Port Driver 2.12.28](https://ftdichip.com/drivers/d2xx-drivers/) (serial port drivers for HARP devices)
   * To download the installer, click *available as a setup executable*.
 * [Spinnaker SDK 1.29.0.5](https://www.flir.co.uk/support/products/spinnaker-sdk/#Downloads) (device drivers for FLIR cameras, sign in required, look in the archived stable versions for 1.29.0.5 64-bit full install)

## Installation
To set up a Bonsai environment to run a sequence, use a terminal to clone the hypnose repo into a local folder:

```
git clone https://github.com/SainsburyWellcomeCentre/hypnose.git
```

Now navigate into `hypnose/.bonsai` and run the `Setup.ps1` script (on Windows right-click >> Run with powershell). Once all dependencies have been restored Bonsai can be launched in a local environment from the `.exe` in this folder. Workflows can be found in the `src` folder.

## SequenceSandbox
The SequenceSandbox.bonsai workflow provides a sandbox for testing behavioral session types (e.g. singles, doubles, free-run). The Bonsai workflow itself has two parameters. One is an an initiation key (the keyboard input that will initiate the session) and the other is a .yml session settings file. This .yml file defines the experiment metadata, the named commands that can be sent to the olfactometer, and the command sequences that are presented during the experiment.

### Session Settings
Experiment parameters are based on a data schema `data-schema`. The data schema defines global experiment parameters such as animal ID information, logging paths etc. It also defines the valve states of named olfactometer commands in `olfactometerCommands` and sequence definitions in `sequences`. Sequences define the order of allowed odours in a particular trial and refer to the named olfactometer commands to produce these sequences. Implementations of these schemas are defined in `.yml` files provided by the user that are then loaded into the Bonsai workflow to set up experiment parameters.

#### Working with data schemas in Visual Studio Code
 To create and edit schema implementations with full autcomplete and hinting, Visual Studio Code requires some extensions to be added:
 * json (ZainChen.json)
 * JSON Schema Validator (tberman.json-schema-validator)
 * YAML (redhat.vscode-yaml)

#### Creating an experiment parameter file
To create an experiment parameter file based on the `data-schema`, create a new `.yml` file and add a reference to the `data-schema` at the top of the file:

 ```
 %YAML 1.1
 ---
 # yaml-language-server: $schema=data-schema.json
 ```

 Below this add your experiment definition. There are 3 main groups of parameters to define: 1) metadata, 2) olfactometerCommands and 3) sequences. An example implementation is shown below:

#### Updating schema files for Bonsai serialization
When schema files are modified, you need to regenerate the corresponding C# serialization classes for Bonsai to properly load and validate the YAML files. This process uses the `dotnet bonsai.sgen` command to generate strongly-typed classes from JSON schema definitions.

To update serialization classes after modifying a schema file, navigate to the location where dotnet was set up (typically the `.bonsai` directory where the Bonsai environment was installed) in a terminal and run:

```
dotnet bonsai.sgen --schema ./src/sequence-schema.json --namespace SequenceSchema
```

For the data schema, use:

```
dotnet bonsai.sgen --schema ./src/data-schema.json --namespace DataSchema
```

**Important:** The version of `bonsai.sgen` used is critical for compatibility. Ensure you're using the same version that was installed with your Bonsai environment setup to avoid serialization conflicts or incompatibilities with the workflow runtime.

This command will:
- Read the JSON schema file specified by `--schema`
- Generate corresponding C# classes in the specified `--namespace`
- Create or update the serialization classes in the `Extensions` folder

The generated classes enable Bonsai to deserialize YAML configuration files with proper type checking and validation based on the schema definitions. Always regenerate these classes when you modify the schema files to ensure consistency between your YAML configurations and the Bonsai workflow expectations.

```
 metadata:
  animalId: plimbo
  rootPath: test
  minimumSampleTime: 0.1
  sampleOffsetTime: 0.1
  loggingRootPath: C:\Users\neurogears\source\repos\swc\hypnose\temp_data

olfactometerCommands:
  - {name: Default, valvesOpenO0: [], valvesOpenO1: [3], endValvesOpenO0: [], endValvesOpenO1: [1], targetFlowO0: [0, 0, 0, 0, 10], targetFlowO1: [0, 0, 0, 10, 10]}
  - {name: Purge, valvesOpenO0: [], valvesOpenO1: [], endValvesOpenO0: [0, 1], endValvesOpenO1: [1], targetFlowO0: [0, 0, 0, 0, 10], targetFlowO1: [0, 0, 0, 10, 10]}
  - {name: OdorA, valvesOpenO0: [0], valvesOpenO1: [], endValvesOpenO0: [0], endValvesOpenO1: [0], targetFlowO0: [10, 0, 0, 0, 10], targetFlowO1: [0, 0, 0, 0, 10]}
  - {name: OdorB, valvesOpenO0: [1], valvesOpenO1: [], endValvesOpenO0: [0], endValvesOpenO1: [0], targetFlowO0: [0, 10, 0, 0, 10], targetFlowO1: [0, 0, 0, 0, 10]}
  - {name: OdorC, valvesOpenO0: [2], valvesOpenO1: [], endValvesOpenO0: [0], endValvesOpenO1: [0], targetFlowO0: [0, 0, 10, 0, 10], targetFlowO1: [0, 0, 0, 0, 10]}
  - {name: OdorD, valvesOpenO0: [3], valvesOpenO1: [], endValvesOpenO0: [0], endValvesOpenO1: [0], targetFlowO0: [0, 0, 0, 10, 10], targetFlowO1: [0, 0, 0, 0, 10]}
  - {name: OdorE, valvesOpenO0: [], valvesOpenO1: [0], endValvesOpenO0: [1], endValvesOpenO1: [0], targetFlowO0: [0, 0, 0, 0, 10], targetFlowO1: [10, 0, 0, 0, 10]}
  - {name: OdorF, valvesOpenO0: [], valvesOpenO1: [1], endValvesOpenO0: [1], endValvesOpenO1: [0], targetFlowO0: [0, 0, 0, 0, 10], targetFlowO1: [0, 10, 0, 0, 10]}
  - {name: OdorG, valvesOpenO0: [], valvesOpenO1: [2], endValvesOpenO0: [1], endValvesOpenO1: [0], targetFlowO0: [0, 0, 0, 0, 10], targetFlowO1: [0, 0, 10, 0, 10]}

sequences:
  - {name: FreeRun,
    defaultCommand: Default,
    presentationTime: 0.8,
    interCommand: Purge,
    interCommandTime: 0.2,
    repeatCount: 20,
    maximumTime: 5,
    rewardCondition1: [
      [{command: OdorA, rewarded: True}, {command: OdorB, rewarded: False}, {command: OdorC, rewarded: False}, {command: OdorD, rewarded: False}, {command: OdorE, rewarded: False}, {command: OdorF, rewarded: False}, {command: OdorG, rewarded: False}],
    ],
    rewardCondition2: [
      [{command: OdorA, rewarded: False}, {command: OdorB, rewarded: False}, {command: OdorC, rewarded: False}, {command: OdorD, rewarded: False}, {command: OdorE, rewarded: True}, {command: OdorF, rewarded: False}, {command: OdorG, rewarded: False}],
    ]}
  - {name: Triples1,
    defaultCommand: Default,
    presentationTime: 0.8,
    interCommand: Purge,
    interCommandTime: 0.2,
    repeat: 0,
    interTrialInterval: 20,
    enableTrialIndicator: True,
    enableRewardLocationIndicator: True,
    rewardCondition1: [
      [{command: OdorC, rewarded: False}, {command: OdorD, rewarded: False}, {command: OdorE, rewarded: False}, {command: OdorF, rewarded: False}, {command: OdorG, rewarded: False}],
      [{command: OdorC, rewarded: False}, {command: OdorD, rewarded: False}, {command: OdorE, rewarded: False}, {command: OdorF, rewarded: False}, {command: OdorG, rewarded: False}],
      [{command: OdorA, rewarded: True}]
    ],
      rewardCondition2: [
      [{command: OdorC, rewarded: False}, {command: OdorD, rewarded: False}, {command: OdorE, rewarded: False}, {command: OdorF, rewarded: False}, {command: OdorG, rewarded: False}],
      [{command: OdorC, rewarded: False}, {command: OdorD, rewarded: False}, {command: OdorE, rewarded: False}, {command: OdorF, rewarded: False}, {command: OdorG, rewarded: False}],
      [{command: OdorB, rewarded: True}]
    ]
    }
```