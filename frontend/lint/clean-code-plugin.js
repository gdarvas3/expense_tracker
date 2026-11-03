/**
 * Oxlint JS plugin enforcing AGENTS.md §6.2: no lambdas.
 * Arrow functions and anonymous function expressions are reported; use named functions.
 */

function isMethod(node) {
  const parent = node.parent
  return parent.type === 'MethodDefinition' || (parent.type === 'Property' && parent.method)
}

const noLambdas = {
  meta: {
    type: 'suggestion',
    docs: { description: 'Disallow arrow functions and anonymous function expressions.' },
    messages: {
      lambda: 'Use a named function instead of a lambda (AGENTS.md §6.2).',
    },
  },
  create(context) {
    function reportArrowFunction(node) {
      context.report({ node, messageId: 'lambda' })
    }

    function reportAnonymousFunction(node) {
      if (node.id === null && !isMethod(node)) {
        context.report({ node, messageId: 'lambda' })
      }
    }

    return {
      ArrowFunctionExpression: reportArrowFunction,
      FunctionExpression: reportAnonymousFunction,
    }
  },
}

export default {
  meta: { name: 'clean-code' },
  rules: { 'no-lambdas': noLambdas },
}
