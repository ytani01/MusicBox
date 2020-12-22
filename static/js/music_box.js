/**
 *
 */

/**
 *
 */
const url = "ws://127.0.0.1:8881";
console.log(`url=${url}`);

let msg = {cmd: '', ch: []};

const single_play = (key) => {
    console.log(`key=${key}`);

    msg['cmd'] = 'single_play';
    msg['ch'] = [key];

    msg_json = JSON.stringify(msg);

    let ws = new WebSocket(url);

    ws.onopen = function (event) {
        console.log(event);
        ws.send(msg_json);

        ws.onclose = function () {
            console.log('closed');
        };
    };
};
