-- Tabela de Produtos
create table if not exists produtos (
    id bigint primary key generated always as identity,
    nome text not null,
    preco_custo numeric,
    preco_venda numeric,
    quantidade integer default 0,
    minimo_alerta integer default 5,
    detalhes text,
    categoria text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Tabela de Vendas
create table if not exists vendas (
    id bigint primary key generated always as identity,
    local_id integer,
    data_hora text,
    total_venda numeric,
    lucro_total numeric,
    cliente text,
    vendedor_nome text,
    itens jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Tabela de Usuários
create table if not exists usuarios (
    id bigint primary key generated always as identity,
    usuario text unique,
    nome_completo text,
    senha text,
    cargo text,
    status text default 'ativo',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Tabela de Licenças (NOVO)
-- Controla quem pagou a mensalidade.
create table if not exists licencas (
    id bigint primary key generated always as identity,
    cliente_id text not null unique,
    -- Email ou Telefone do dono
    data_validade date not null,
    status text default 'ativo',
    -- ativo, expirado, bloqueado
    plano text default 'pro',
    -- basico, pro
    ultimo_pagamento date,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- RLS
alter table produtos enable row level security;
alter table vendas enable row level security;
alter table usuarios enable row level security;
alter table licencas enable row level security;
-- Policies (Permissiva para MVP)
create policy "Acesso Total Produtos" on produtos for all using (true);
create policy "Acesso Total Vendas" on vendas for all using (true);
create policy "Acesso Total Usuarios" on usuarios for all using (true);
create policy "Acesso Total Licencas" on licencas for all using (true);