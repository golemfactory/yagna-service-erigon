Cypress.Commands.add('startNewNodeClick', (text = 'Start new node') => cy.contains(text, { matchCase: false }).click());

Cypress.Commands.add('notifyProceedMetamaskLogin', () => {
  cy.startNewNodeClick();

  cy.get('.Toastify__toast--error')
    .invoke('text')
    .then((text) => expect(text).to.equal('Proceed with MetaMask login!'));
});
