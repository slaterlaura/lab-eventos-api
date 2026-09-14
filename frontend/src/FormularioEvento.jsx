import { useState } from "react";
import { criarEvento } from "./api.js";

const VAZIO = { nome: "", data: "", local: "", vagas: "" };

export default function FormularioEvento({ onCriado }) {
  const [campos, setCampos] = useState(VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  function atualizarCampo(nome, valor) {
    setCampos((atual) => ({ ...atual, [nome]: valor }));
  }

  async function enviar(evento) {
    evento.preventDefault();

    setEnviando(true);
    setErro(null);

    try {
      const novo = await criarEvento({
        ...campos,
        vagas: Number(campos.vagas),
      });

      setCampos(VAZIO);
      onCriado(novo);
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="formulario cartao" onSubmit={enviar}>
      <h2>Novo evento</h2>

      <div className="linha">
        <label className="campo">
          Nome
          <input
            value={campos.nome}
            onChange={(e) => atualizarCampo("nome", e.target.value)}
          />
        </label>

        <label className="campo">
          Data
          <input
            type="date"
            value={campos.data}
            onChange={(e) => atualizarCampo("data", e.target.value)}
          />
        </label>
      </div>

      <div className="linha">
        <label className="campo">
          Local
          <input
            value={campos.local}
            onChange={(e) => atualizarCampo("local", e.target.value)}
          />
        </label>

        <label className="campo">
          Vagas
          <input
            type="number"
            value={campos.vagas}
            onChange={(e) => atualizarCampo("vagas", e.target.value)}
          />
        </label>
      </div>

      <button className="botao" type="submit" disabled={enviando}>
        {enviando ? "Enviando…" : "Criar evento"}
      </button>

      {erro && <p className="erro" role="alert">{erro}</p>}
    </form>
  );
}
