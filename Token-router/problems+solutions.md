1. There is an issue where the wrong models were chosen for the wrong tasks 
Soln : We are now labelling all the models so that at the time of invocation we know what tasks should we send it to depending on the size of the task

2. We are now hitting rate limits 
Soln : We will now have a pre processing step which will automatically route the available models and then the llm can take a desicion on what to do based ont he models which it has recieved

What is rpm tpm rpd tpd