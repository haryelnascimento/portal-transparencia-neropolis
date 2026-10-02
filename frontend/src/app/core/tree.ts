export interface TreeNode { code: string; name: string; parent: string | null }

/**
 * Filhos de um nó. Quando um nível tem um único filho (ex.: "Aplicações Diretas" ou o mesmo item repetido
 * no nível seguinte), ele é pulado: o cidadão vê sempre uma escolha real a cada clique.
 */
export function childrenOf<T extends TreeNode>(nodes: T[], parent: string | null): T[] {
  let children = nodes.filter(n => n.parent === parent);
  while (children.length === 1 && nodes.some(n => n.parent === children[0].code)) {
    children = nodes.filter(n => n.parent === children[0].code);
  }
  return children;
}

export function hasChildren(nodes: TreeNode[], code: string) {
  return nodes.some(n => n.parent === code);
}

/** Ancestrais visíveis (do mais geral ao mais específico), omitindo níveis de filho único. */
export function ancestorsOf<T extends TreeNode>(nodes: T[], code: string): T[] {
  const byCode = new Map(nodes.map(n => [n.code, n]));
  const chain: T[] = [];
  for (let node = byCode.get(code); node?.parent; ) {
    node = byCode.get(node.parent);
    if (node) chain.unshift(node);
  }
  return chain.filter(node => childrenOf(nodes, node.parent).includes(node));
}

/** Código de modalidade "90 – Aplicações Diretas": gasto feito pela própria Prefeitura (ex.: 3.3.90.00.00.00). */
export function isDirectApplication(code: string) {
  const parts = code.split('.');
  return parts[2] === '90' && parts.slice(3).every(p => /^0+$/.test(p));
}

/**
 * Filhos na árvore de natureza da despesa, dissolvendo o nível "Aplicações Diretas": os elementos de gasto
 * (salários, serviços, obras…) aparecem direto sob o grupo, e só as transferências a terceiros ficam agrupadas.
 */
export function natureChildrenOf<T extends TreeNode>(nodes: T[], parent: string | null): T[] {
  return childrenOf(nodes, parent).flatMap(child => (isDirectApplication(child.code) && hasChildren(nodes, child.code) ? childrenOf(nodes, child.code) : [child]));
}

/** Rótulo legível para a modalidade 91 (intraorçamentária), cujo nome oficial é longo e técnico. */
export function natureLabel(node: { code: string; name: string }) {
  const parts = node.code.split('.');
  return parts[2] === '91' && parts.slice(3).every(p => /^0+$/.test(p)) ? 'Entre órgãos da própria Prefeitura' : node.name;
}
