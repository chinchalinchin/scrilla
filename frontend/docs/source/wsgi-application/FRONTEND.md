# Frontend
The frontend is a standard [Angular](https://angular.io/docs) project generated through the `ng` cli utility. In addition, [Angular Material](https://material.angular.io/) has been installed for added user interface functionality.

In development, the <b>Angular</b> development server `ng serve` is used to serve up the assets. When the app is containerized, an <b>nginx</b> container is used to serve up the webpack bundles resulting from `ng build --prod --output-hashing none`. 

In addition, the documentation (which you are currently reading) was generated with a Python library, <b>[sphinx](https://www.sphinx-doc.org/en/master/)</b>. The documentation must be built before the <b>Angular</b> can compile, since the <i>angular.json</i> expects the artifacts of the documentation build to exist in in its <i>src/assets</i> directory in the frontend project root.

## Setup

### Python Dependencies

In the <i>/frontend/docs/</i> directory, you will find a <i>requirements.txt</i> file that contains the dependencies needed to build the documentation. Activate your virtual environment, if using one and then nstall these dependencies through <b>pip/pip3</b>,

`pip3 install -r requirements`

### Sphinx Documentation

Once the dependencies are installed, the documentation can be built from the <i>/frontend/docs</i> directory with,

`make html`

The generated html, css and js files will be deposited into the <i>/frontend/docs/build/html/</i> folder. These files need manually copies into the Angular assets folder at <i>/frontend/pynance-web/src/assets/docs/</i>,

`cp /frontend/docs/build/html/ /frontend/pynance-web/src/assets/docs/`

### Node Dependencies

The next step is to install the <b>NodeJS</b> dependencies and the <b>Angular CLI</b>. Navigate to the <i>/frontend/pynance-web/</i> directory and execute,

`npm install @angular/cli`<br>
`npm install`

### Angular Development Server

The final step is to launch the <b>Angular</b> development server. From the <i>/frontend/pynance-web/</i> directory, execute,

`ng serve`

### <i>web-server</i> Script

All of the above steps have been bundled into a shell script in the <i>/scripts/server/</i> directory. To perform all of the above steps, simply execute,

`./scripts/server/web-server.sh`

Instead of manually entering each command along the way. 

### Backend Services

TODO

In development, the <b>Angular</b> app communicates directly with the backend. In other words, when the <b>Angular</b> app is served up locally into a client browser, the service calls ping the backend server directly. This is not how the application runs when containerized. See [nginx Deployment](#nginx-Deployment) below for more information on the service configuration in a containerized environment.

### Components

TODO

### nginx Deployment

A <b>Dockerfile</b> in the <i>/frontend/</i> directory isolates the application dependencies, generates the <b>Sphinx</b> documentation and builds the <b>Angular</b> application before finally deploying it onto an <b>nginx</b> container. 

Note, when the frontend is containerized, <b>Angular</b> does not directly communicate with the backend. Instead, the <b>nginx</b> server inside of the container is configured to proxy all requests made to the <i>/api/</i> path back to the <b>Django</b> application server. The client therefore sends all requests back to the frontend server, which in turns mediates access to the backend server.

The frontend container can be launched by supplying an argument of <i>--container</i> to the <i>web-server.sh</i> script,

`./scripts/server/web-server.sh --container`

The backend must be running or else the <b>nginx</b> server will fail due to the <b>upstream</b> server set in the <i>/frontend/server/nginx.conf</i> file,

> upstream pynance{<br>
>        server $APP_HOST:$APP_PORT fail_timeout=60s;<br>
>   }<br>

Note, the <b>APP_HOST</b> and <b>APP_PORT</b> environment variables must point to the location and port on which the backend server is running.

If you wish to run the frontend in standalone mode without the backend (be aware, none of the Angular components will function properly), remove these lines from the <i>nginx.conf</i>. 

### Notes

1. Due to the way Angular's development server refresh works, changes made to the documentation will not get displayed through the development server when they are committed. Sphinx needs to repackage the new markdown files into static assets and Angular needs to repack those assets into webpack bundles. The development server must be restarted entirely and the documentation rebuilt if changes are made to the documentation.
