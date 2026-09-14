const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function mensagemDeErro(resposta) {
  const corpo = await resposta.json();

  // HTTPException: uma string
  if (typeof corpo.detail === "string") return corpo.detail;

  // 422 do Pydantic: uma lista, um item por campo
  if (Array.isArray(corpo.detail)) {
    return corpo.detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join(" · ");
  }

  return `Erro ${resposta.status} ao falar com a API.`;
}

export async function listarEventos() {
  const resposta = await fetch(`${API_URL}/eventos`);

  if (!resposta.ok) {
    throw new Error(`Erro ${resposta.status} ao buscar os eventos.`);
  }

  return resposta.json();
}

export async function criarEvento(dados) {
  const resposta = await fetch(`${API_URL}/eventos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });

  if (!resposta.ok) {
    throw new Error(await mensagemDeErro(resposta));
  }

  return resposta.json();
}

export async function enviarCartaz(eventoId, arquivo) {
  const dados = new FormData();
  dados.append("arquivo", arquivo);

  const resposta = await fetch(`${API_URL}/eventos/${eventoId}/cartaz`, {
    method: "POST",
    body: dados,
  });

  if (!resposta.ok) throw new Error(await mensagemDeErro(resposta));

  return resposta.json();
}
