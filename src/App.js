import React from "react";
import Component from "@reach/component-component";

const example = `
;;deftype containers tosca.nodes.docker.Container

;;- int y
;;- int my_array [5]
;;- my_array[1] = 3232
;;- y = 31

;;for c in containers
(and
  (< c.ip_address 192.168.1.150)
  (< c.mem_size 2GB)
  (= c.nodeType 'nodePort')
)
;;endfor
`;

const URL =
  process.env.NODE_ENV === "production"
    ? "http://editorapi:5000/api/run"
    : "/api/run";

console.log({ URL, env: process.env });

export default () => (
  <Component initialState={{ rawInput: example, smtlib: "", rpls: 0 }}>
    {({ setState, state }) => (
      <div style={{
        height: '100vh'
      }}>
        <div className="row" style={{ height: '6vh', textAlign: 'center'}}>
        <div className="col-sm-12">
        <h1>
            Sugar Syntax{" "}
            <span role="img" aria-label="emoji-stars">
              ✨
            </span>{" "}
            Live
            <span role="img" aria-label="emoji-laptop">
              👨🏻‍💻
            </span>
          </h1>
        </div>
          
        </div>
        <div className="row">
          <div className="col-lg-6" style={{background: '#f8f8f8', height:'94vh'}}>
            <textarea
              id="code"
              defaultValue={state.rawInput}
              onChange={({ target: { value } }) => {
                setState({ rawInput: value });
                fetch(URL, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ data: value })
                })
                  .then(res => res.text())
                  .then(response => {
                    setState({ smtlib: response });
                  })
                  .catch(err => {
                    setState({ smtlib: err.message });
                  });
              }}
              style={{height: '100%', width: '100%'}}
              className="form-control"
            />
          </div>
          <div className="col-lg-6">
            <pre>{state.smtlib}</pre>
          </div>
        </div>
      </div>
    )}
  </Component>
);
