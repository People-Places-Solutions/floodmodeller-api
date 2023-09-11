# Flood Modeller Python API Toolbox (coming soon...)
This toolbox served as a place to store and maintain production-ready tools that integrate with the Flood Modeller Python API.

Tools will sit under the following categories:
|Category | Description |
|---------|-------------|
|[Results Analysis](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/results_analysis)| Details
|[Model Build](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/model_build)| Details
|[Model Conversion](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/model_conversion)| Details
|[Visualisation](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/visualisation)| Details
|[Model Review](https://github.com/People-Places-Solutions/floodmodeller-api/tree/main/toolbox/model_review)| Details

These tools act as standalone scripts. To run them, please read the available documentation for each tool. 

# Developing Custom Tools
You can develop your own tools to integrate with the Flood Modeller Python API!

There are a few conventions you need to follow to do this.
- Add a python file to one of the directories in the toolbox
- Within the file, define the tool as single function
- Within the same file, create a child class of FMTool, passing in the tool name and description, funciton to be run and the function parameters

See the [example_tool.py](example_tool.py) script for an example of how to do this.
