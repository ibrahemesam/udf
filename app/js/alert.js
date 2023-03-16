window.alert = (info, bold = true) => {
  let modal = $(`
    <div
      class="modal fade"
      data-backdrop="static"
      data-keyboard="false"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <!-- Modal body -->
          <div class="modal-body ${(() => {
            if (bold) return "font-weight-bolder font-size-medium";
            return "";
          })()}" style="text-align: center; font-size: x-large;">
            <pre
            class="m-0 ${(() => {
              if (!bold) return "font-weight-bold";
              return "";
            })()}"
            style="white-space: pre-line; ${(() => {
              if (!bold) return "font-size: initial";
              return "";
            })()}">${info}</pre>
          </div>

          <!-- Modal footer -->
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary m-auto close"
              data-dismiss="modal"
            >
              Ok
            </button>
          </div>
        </div>
      </div>
    </div>
    `);
  let btn_ok = modal.find("button.close");
  modal.on("shown.bs.modal", (evt) => btn_ok.focus());
  let _on_ok_promise = new Promise(
    (resolve) => (modal._on_ok_promise_resolve = resolve)
  );
  modal.on("hidden.bs.modal", (evt) => {
    modal.remove();
    modal._on_ok_promise_resolve();
  });
  modal.modal("show");

  btn_ok.on("click", (evt) => {
    window.removeEventListener("keypress", modal.on_Enter_keypress, false);
  });
  modal.on_Enter_keypress = (evt) => {
    if (evt.code == "Enter") {
      btn_ok.click();
    }
  };
  window.addEventListener("keypress", modal.on_Enter_keypress);
  return _on_ok_promise;
};
