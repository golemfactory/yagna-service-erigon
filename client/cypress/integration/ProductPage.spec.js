/// <reference types="cypress" />

describe('Erigolem Product Page tests', () => {
  beforeEach(() => {
    cy.visit('https://erigon.golem.network/');
  });

  it('Displays Product Page', () => {
    cy.contains('Run ethereum nodes in seconds');
    cy.contains(
      'Erigolem is one of the fastest ways to integrate into the ethereum network. Select the type of network, click "start" and enjoy access to the most popular blockchain network in the world. Done.',
    );
  });

  it('Checks if Metamask installation link is correct', () => {
    cy.contains('Install Metamask').should('have.attr', 'href', 'https://metamask.io/');
  });

  it('Checks if Metamask login notification works', () => {
    cy.notifyProceedMetamaskLogin();
  });
});
