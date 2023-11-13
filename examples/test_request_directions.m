%% Set matlab - python connection
% insert here the path to the python.exe file from your hackaton
% environment
% e.g.: pyenv("Version","C:\Users\broggi\AppData\Local\anaconda3\envs\hackaton\python.exe")
pyenv("Version","C:\Users\mbroggi\anaconda3\envs\hackaton\python.exe");

%% import necessary modules into matlab
directions = py.importlib.import_module("hackaton_directions");
ors = py.importlib.import_module("openrouteservice");
numpy = py.importlib.import_module("numpy");
ors_client = ors.client.Client(pyargs('key','5b3ce3597851110001cf6248284dda70a52642d5bdfdd69bc4bba086'));
% Connect to the OpenRouteService API client. Use pyargs to generate 
% key/value input pairs. Insert your API key here.


%% Test the direction request without points avoidance
startpoint = [12.115737, 54.084774];
endpoint = [12.072063, 54.103684];

% convert the matlab arrays to a python list to call the driving direction
% function. The output is a python tuple that requires some post-processing
py_out = directions.driving_directions(ors_client,py.list(startpoint),py.list(endpoint));

% post-process the data into matlab
% convert python list of lists into a numpy array and then to a matlab double
steps_orig = double(numpy.array(py_out{1})); % sequence of coordinates constructing a path on the map
% convert python dictionary to a structure
summary_orig = py_out{2}.struct(); % overview of the route (distance and duration)

%% Test the direction request with points avoidance
% As an example of avoidance, we import the informations on the roadworks
% in the city of Rostok.

% Request JSON with roadwork infor
headers = {'Content-Type' 'application/json'; 'Accept' 'application/json'};
options = weboptions('HeaderFields',headers);
json_roadwork = webread('https://geo.sv.rostock.de/download/opendata/baustellen/baustellen.json', options);
% extract roadworks coordinates
struct_roadwork = [json_roadwork.features(:).geometry];
roadwork_coord = [struct_roadwork.coordinates]';

% convert the matrix with the roadwork coordinates to a python list of 
% lists by intermediately going to a numpy array
npa_temp = numpy.asarray(roadwork_coord);

% ask the directions avoiding roadworks
py_out = directions.driving_directions_avoiding_points(ors_client,py.list(startpoint),py.list(endpoint),npa_temp.tolist() );

steps_norw = double(numpy.array(py_out{1}));
summary_norw = py_out{2}.struct();
%% Some plots
% Plot the route without avoidance and add the roadworks.
% Note that the direction API gives longitude first and latitude second...
geoplot(steps_orig(:,2),steps_orig(:,1),'r');  hold on;
lims = [0.9999*min(steps_orig);1.0001*max(steps_orig)]; % just enlarge sligthly the plot area
geolimits(lims(:,2)',lims(:,1)')
% add the roadworks
geoplot(roadwork_coord(:,2),roadwork_coord(:,1),'bx')
% Plot the route avoiding roadworks
geoplot(steps_norw(:,2),steps_norw(:,1),'g');
legend('Original route','Road works','Alternative route')
