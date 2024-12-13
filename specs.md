# General specs / task list

## Videography
- Delay buffering of logging of video frames dependent on beam breaks (real or simulated). Frames within a settable time window around beam break are logged to disk. Initially just record everything, later will need to be event-triggered

## Odour delivery
- Odour delivery and switching protocol, initially by default with vacuum line

## Schema API
- Includes a mapping/naming definition (e.g. line1 --> odorA, poke1 --> left)
- Properties for all relevant acquisition and logging parameters (camera frame rate, experiment metadata, logging path etc.)
- Each rule should have an individual file (discrimination, doubles, free-run etc.)
- Rule file describes (in abstract) the sequence of odors and the reward targets
- Rule file should have option to either explicitly select odor sequence, or randomise it according to rule parameters (e.g. no two odours repeated in sequence)
- Session rules including max. length of a session or max rewards in a session, reaching criterion
- Flexible enough to make adjustments to the structure of e.g. the hidden rule
- To generalise, a rule file specifies 1. The allowed set of odours, 2. The sequence rule for those odours (number in sequence, which odours can follow other odours), 3. Which odours in the sequence are targets for reward
- Schema API should be able to construct all the trial types listed in the schema

## Bonsai consumption of API
- Automatically sets all relevant parameters to hardware (camera settings, logging path etc.)
- Ability to switch rules manually for testing, as well as automatically based on animal performance during an inter-trial period

## Graphical interface
- Clickable square interactors for valves to switch state, line name dynamically loaded from parameter schema / mapping file
- Circle interactors for state of poke IR, name dynamically loaded from parameter schema / mapping file
- Diamond interactors for lick state, name dynamically loaded from parameter schema / mapping file
- Cross interactors for LED activation state in polke, name dynamically loaded from parameter schema / mapping file
- Additional interactor for pump state
- Color convention: grey for low, white for high
- Interaction: click to switch state. In cases where state switch requires animal input (e.g. IR poke) interaction simulates the state switch
- Assign each odor valve a keyboard shortcut dynamically from parameter schema / mapping file
- Drop-down menu that allows for manually assigning a rule, or displays the current rule if automatic transition. Should have a visual representation of the current trial sequence, and the reward target
- Session information (number of pokes that resulted in odor delivery, total beam crossings, entrances to reward ports that resulted in reward, entrances to reward ports, current rule, current and next odor stimulus, upcoming rule, time in session,mouse name)
- Camera video feed
- Button or hotkey to gracefully exit the workflow

## Logging and post-processing
- Raw log of all events to local hard drive
- Robocopy subprocess for automated data transfer to network drive
- Neuroblueprint/datashuttle format*
- Video logging
- Postprocessing script to organise data (post-hoc) by beam crossings / trial initiations. All available data synchronised and accessible, visualisable