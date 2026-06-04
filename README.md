LUMIERESENVILLE — ROUTES & DATA FORMATS
=======================================


ROUTES 

/api en préfix
------

Semaphore
  GET    /list_semaphore
  GET    /semaphore/{id}
  POST   /add_semaphore
  PUT    /update_semaphore/{id}
  GET    /list_node
  POST   /add_node
  PUT    /update_node/{id}

Robot
  GET    /list_robots
  GET    /robot/{id}
  GET    /robot/{id}/mission
  POST   /add_robot
  PUT    /update_robot/{id}

Mission
  GET    /list_missions
  POST   /add_mission
  PUT    /update_mission/{id}

Team
  GET    /list_teams
  POST   /add_team
  PUT    /update_team/{id}


DATA FORMATS
------------

Semaphore
{
  "id": "uuid",
  "name": "string",
  "state": "Available | Occupied | Disabled",
  "duration": 30
}

Robot
{
  "id": "uuid",
  "name": "string",
  "state": "Available | Occupied | Disabled",
  "speed": 1.5,
  "position_x": 12.0,
  "position_y": 4.75
}

Mission
{
  "id": "uuid",
  "name": "string",
  "semaphore_id": "uuid",
  "robot_id": "uuid",
  "state": "Pending | In progress | Done",
  "start_date": "text",
  "end_date": "text",
  "team": "text"
}

Team
{
  "id": "uuid",
  "name": "text",
  "ip": "text",
  "allowed": true
}

Shape
{
  "id": "uuid",
  "name": "string",
  "image": "text"
}