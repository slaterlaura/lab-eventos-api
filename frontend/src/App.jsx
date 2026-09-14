import { useCallback, useEffect, useState } from "react";
import { listarEventos } from "./api.js";
import FormularioEvento from "./FormularioEvento.jsx";
import EnviarCartaz from "./EnviarCartaz.jsx";
import "./App.css";

export default function App() {
  const [eventos, setEventos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);

    try {
      setEventos(await listarEventos());
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  function atualizarEvento(atualizado) {
    setEventos((atual) =>
      atual.some((e) => e.id === atualizado.id)
        ? atual.map((e) => (e.id === atualizado.id ? atualizado : e))
        : [...atual, atualizado],
    );
  }

  return (
    <div>
      <h1>Eventos do Campus</h1>

      <FormularioEvento onCriado={atualizarEvento} />

      <h2>Eventos cadastrados</h2>

      {carregando && <p className="vazio">Carregando eventos…</p>}

      {!carregando && erro && (
        <p className="erro" role="alert">
          {erro} <button onClick={carregar}>Tentar de novo</button>
        </p>
      )}

      {!carregando && !erro && eventos.length === 0 && (
        <p className="vazio">Nenhum evento cadastrado ainda.</p>
      )}

      {!carregando && !erro && eventos.length > 0 && (
        <ul className="lista-eventos">
          {eventos.map((evento) => (
            <li key={evento.id} className="evento cartao">
              <div className="evento-cartaz">
                {evento.cartaz_url ? (
                  <img src={evento.cartaz_url} alt={evento.nome} />
                ) : (
                  <span className="evento-cartaz-vazio">Sem cartaz</span>
                )}
              </div>

              <div className="evento-info">
                <h3>{evento.nome}</h3>
                <p className="evento-detalhes">
                  {evento.data} · {evento.local} · {evento.vagas} vagas
                </p>

                <EnviarCartaz
                  eventoId={evento.id}
                  temCartaz={Boolean(evento.cartaz_url)}
                  onEnviado={atualizarEvento}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
