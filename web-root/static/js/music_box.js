/**
 *
 */
const dst_host = location.hostname;
const dst_port = 8880;
const dst_url = `ws://${dst_host}:${dst_port}/`;
console.log(`dst_url=${dst_url}`);

const ws_send = function (msg) {
    msg_str = JSON.stringify(msg);
    //console.log(`ws_send(${msg_str})`);

    let ws = new WebSocket(dst_url);

    ws.onopen = function () {
        // console.log(`ws.onopen()`);
        ws.send(msg_str);
        console.log(`ws.send(${msg_str})`);
    };

    ws.onclose = function () {
        // console.log(`ws.onclose()`);
    };
};

const single_play = function (ch_list) {
    console.log(`single_play([${ch_list}])`);

    msg = {cmd: "single_play", ch: ch_list};
    ws_send(msg);
};

const calibrate = function (ch, on, pw_diff, tap) {
    console.log(`calibrate(${ch},${on},${pw_diff},${tap})`);

    msg = {cmd: "calibrate",
           ch: ch, on: on, pw_diff: pw_diff, tap: tap};
    ws_send(msg);
};
