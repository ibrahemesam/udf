window.ask = (
  title,
  body,
  options = {
    yes: { color: "success", text: "yes" },
    no: { color: "danger", text: "no" },
  }
) => {
  let modal = $(`
        <div
          class="modal fade"
          id="modal-whatsapp-send"
          data-backdrop="static"
          data-keyboard="false"
        >
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <!-- Modal Header -->
              <div class="modal-header" style="position: relative">
                <h4 class="modal-title font-weight-bold col-12" style="
                text-align: center;
                font-size: xx-large;
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                padding-top: 6px;
                ">
                  ${title}
                </h4>
              </div>

              <!-- Modal body -->
              <div class="modal-body font-weight-bolder font-size-large" style="text-align: center; font-size: x-large;">
                <pre class="m-0" style="white-space: pre-line;">${body}</pre>
              </div>

              <!-- Modal footer -->
              <div class="modal-footer">
                <div class="m-auto"></div>
              </div>
            </div>
          </div>
        </div>
        `); //m-auto
  let footer = modal.find("div.modal-footer > div");
  // yes: { color: "success", text: "yes" },
  Object.keys(options).forEach((option_id) => {
    let option = options[option_id];
    $(`
            <button
                type="button"
                class="btn btn-${option.color} font-weight-bold"
            >
                ${option.text}
            </button>
            `)
      .on("click", (evt) => {
        modal.on("hidden.bs.modal", (evt) => {
          modal.remove();
          modal._on_close_promise_resolve(option_id);
        });
        modal.modal("hide");
      })
      .css("margin-right", "6px")
      .appendTo(footer);
  });

  let _on_close_promise = new Promise(
    (resolve) => (modal._on_close_promise_resolve = resolve)
  );

  modal.modal("show");
  return _on_close_promise;
};
