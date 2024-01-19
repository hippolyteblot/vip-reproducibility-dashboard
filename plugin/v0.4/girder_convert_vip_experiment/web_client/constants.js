const STATUSES = {
  INITIALIZING: { order : 0, text: "Initializing"},
  READY:  { order : 10, text: "Ready"},
  RUNNING:  { order : 20, text: "Running"},
  FINISHED:  { order : 30, text: "Completed, results available"},
  INITIALIZATIONFAILED:  { order : 40, text: "Initializing failed"},
  EXECUTIONFAILED:  { order : 50, text: "Execution failed"},
  UNKNOWN:  { order : 60, text: "Unknown"},
  KILLED:  { order : 70, text: "Killed"}
}

export {
  STATUSES
};