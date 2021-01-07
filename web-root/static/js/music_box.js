/**
 * Music Box Web App
 *
 * (c) 2021 Yoichi Tanibayashi
 */
const WsHost = location.hostname;
const DefWsPort = 8880;
console.log(`WsHost:DefWsPort=${WsHost}:${DefWsPort}`);

/**
 * @param {number} port
 */
const get_url = function (port) {
    let url = `ws://${WsHost}:${port}/`;
    return url;
};

/**
 * @param {object} msg
 * @param {number} port
 */
const ws_send = function (msg, port) {
    let msg_str = JSON.stringify(msg);
    console.log(`ws_send(${msg_str}, ${port})`);

    if ( port === undefined ) {
        port = DefWsPort;
    }

    let url = get_url(port);
    console.log(`url=${url}`);

    let ws = new WebSocket(url);

    ws.onopen = function () {
        ws.send(msg_str);
        console.log(`onopen(): ws.send(${msg_str})`);
    };

    ws.onclose = function () {
        // console.log(`ws.onclose()`);
    };
};

/**
 * @param {Array.<number>} ch_list
 * @param {number} port
 */
const single_play = function (ch_list, port) {
    console.log(`single_play([${ch_list}], ${port})`);

    let msg = {cmd: "single_play", ch: ch_list};
    ws_send(msg, port);
};

/**
 * @param {number} ch
 * @param {boolean} on
 * @param {number} pw_diff
 * @param {boolean} tap
 * @param {number} port
 */
const calibrate = function (ch, on, pw_diff, tap, port) {
    console.log(`calibrate(${ch},${on},${pw_diff},${tap},${port})`);

    let msg = {cmd: "calibrate",
               ch: ch, on: on, pw_diff: pw_diff, tap: tap};
    ws_send(msg, port);
};
