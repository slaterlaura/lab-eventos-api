import { useId, useRef, useState } from "react";
import { enviarCartaz } from "./api.js";

export default function EnviarCartaz({ eventoId, temCartaz, onEnviado }) {
  const inputId = useId();
  const inputRef = useRef(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  async function selecionarArquivo(evento) {
    const arquivo = evento.target.files[0];
    if (!arquivo) return;

    setEnviando(true);
    setErro(null);

    try {
      const atualizado = await enviarCartaz(eventoId, arquivo);
      onEnviado(atualizado);
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
      // Sem isso, escolher o MESMO arquivo de novo não dispara onChange.
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="upload-cartaz">
      <label className="upload-cartaz-rotulo" htmlFor={inputId}>
        {temCartaz ? "Trocar cartaz" : "Adicionar cartaz"}
      </label>
      <input
        id={inputId}
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        disabled={enviando}
        onChange={selecionarArquivo}
      />

      {enviando && <span className="upload-cartaz-status">enviando…</span>}
      {erro && <p className="erro" role="alert">{erro}</p>}
    </div>
  );
}
