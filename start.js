const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors for output
const colors = {
    green: '\x1b[32m',
    blue: '\x1b[34m',
    reset: '\x1b[0m'
};

// Function to check if a port is in use
function isPortInUse(port) {
    return new Promise((resolve) => {
        const net = require('net');
        const server = net.createServer();
        server.once('error', () => resolve(true));
        server.once('listening', () => {
            server.close();
            resolve(false);
        });
        server.listen(port);
    });
}

// Function to kill process on a port
async function killPort(port) {
    if (await isPortInUse(port)) {
        console.log(`${colors.blue}Port ${port} is in use. Attempting to kill the process...${colors.reset}`);
        if (process.platform === 'win32') {
            spawn('taskkill', ['/F', '/IM', 'node.exe']);
        } else {
            spawn('lsof', ['-ti', `:${port}`]).stdout.on('data', (data) => {
                spawn('kill', ['-9', data.toString().trim()]);
            });
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

// Function to start a process
function startProcess(command, args, cwd) {
    const process = spawn(command, args, {
        cwd,
        shell: true,
        stdio: 'inherit'
    });

    process.on('error', (error) => {
        console.error(`Error starting process: ${error}`);
    });

    return process;
}

// Main function
async function main() {
    try {
        // Kill any existing processes
        await killPort(3000);
        await killPort(8000);

        // Start backend
        console.log(`${colors.green}Starting backend server...${colors.reset}`);
        const backendDir = path.join(__dirname, 'src');
        
        // Create and activate virtual environment if it doesn't exist
        if (!fs.existsSync(path.join(__dirname, 'venv'))) {
            spawn('python', ['-m', 'venv', 'venv'], { stdio: 'inherit' });
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        // Install requirements
        const pip = process.platform === 'win32' ? 'venv\\Scripts\\pip' : 'venv/bin/pip';
        spawn(pip, ['install', '-r', 'requirements.txt'], { stdio: 'inherit' });
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Start uvicorn
        const python = process.platform === 'win32' ? 'venv\\Scripts\\python' : 'venv/bin/python';
        const backend = startProcess(python, ['-m', 'uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'], backendDir);

        // Start frontend
        console.log(`${colors.green}Starting frontend server...${colors.reset}`);
        const frontendDir = path.join(__dirname, 'frontend');
        spawn('npm', ['install'], { cwd: frontendDir, stdio: 'inherit' });
        await new Promise(resolve => setTimeout(resolve, 2000));
        const frontend = startProcess('npm', ['start'], frontendDir);

        // Handle process termination
        process.on('SIGINT', () => {
            console.log(`\n${colors.blue}Shutting down servers...${colors.reset}`);
            backend.kill();
            frontend.kill();
            process.exit(0);
        });

        // Wait for servers to be ready
        console.log(`${colors.green}Waiting for servers to start...${colors.reset}`);
        while (await isPortInUse(3000) || await isPortInUse(8000)) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        console.log(`${colors.green}Servers are running!${colors.reset}`);
        console.log(`${colors.blue}Frontend: http://localhost:3000${colors.reset}`);
        console.log(`${colors.blue}Backend: http://localhost:8000${colors.reset}`);
        console.log(`${colors.blue}API Documentation: http://localhost:8000/docs${colors.reset}`);
        console.log('\nPress Ctrl+C to stop the servers');

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

main(); 