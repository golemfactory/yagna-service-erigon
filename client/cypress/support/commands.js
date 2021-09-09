import 'cypress-wait-until';

Cypress.Commands.add('startNewNodeClick', (text = 'Start new node') => cy.contains(text, { matchCase: false }).click());

Cypress.Commands.add('notify', (value, type) =>
  cy
    .get(`.Toastify__toast--${type}`)
    .invoke('text')
    .then((text) => expect(text).to.equal(value)),
);

Cypress.Commands.add('notifyProceedMetamaskLogin', () => {
  cy.startNewNodeClick();
  cy.notify('Proceed with MetaMask login!', 'error');
});

Cypress.Commands.add('copyElement', (label) => cy.contains(label).contains('Copy').click());

Cypress.Commands.add('getNode', (label) => cy.contains(label).parents('div[role=node]'));
