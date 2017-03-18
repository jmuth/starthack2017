declare var require: {
    <T>(path: string): T;
    (paths: string[], callback: (...modules: any[]) => void): void;
    ensure: (paths: string[], callback: (require: <T>(path: string) => T) => void) => void;
};

const Hapi: any = require('hapi');

const server = new Hapi.Server();
server.connection({ port: 8080 });

server.start((err: any) => {

    if (err) {
        throw err;
    }
    console.log(`Server running at: ${server.info.uri}`);
});

server.route({
    method: 'GET',
    path: '/compute_video/{keyword}',
    config: {
		handler: function(request: any, reply: any) {
			let keyword: number = request.params.keyword;

			var spawn = require("child_process").spawn;
            var process = spawn('python3',["main.py", keyword]);

            reply(0).header('Access-Control-Allow-Origin', '*');
		}
	}
});