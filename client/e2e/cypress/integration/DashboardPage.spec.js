/// <reference types="cypress" />

describe('Erigolem Dashboard Page tests', () => {
  beforeEach(() => cy.visit(''));

  const newNodeLabel = ' is my new node';
  const tabPanel = 'div[role=tabpanel]';

  it('Displays Dashboard with no new nodes ', () => {
    cy.contains("Ooops! It looks like you don't have any node currently running");
  });

  it('Checks if user can start New Node', () => {
    cy.startNewNodeClick().then(() => {
      cy.contains('Name your node');
      cy.get('input[type=text]').type(newNodeLabel);

      cy.contains('Choose network');
      cy.get('label[for=network_rinkeby]').click();

      cy.startNewNodeClick('Start node').then(() => cy.contains(newNodeLabel));
    });
  });

  it('Checks if user can see his Active Nodes', () => {
    cy.get(tabPanel).should('have.length.at.least', 1);
  });

  it('Checks if New Node is running', () => {
    cy.get(`span[role=status]`)
      .invoke('text')
      .then((text) => text === 'Running');
  });

  it('Checks if user can copy Address', () => {
    cy.copyElement('Address');
    cy.notify('Copied!', 'success');
  });

  it('Checks if user can copy Login', () => {
    cy.copyElement('Login');
    cy.notify('Copied!', 'success');
  });

  it('Checks if user can copy Password', () => {
    cy.copyElement('Password');
    cy.notify('Copied!', 'success');
  });

  it('Checks if user can stop New Node', () => {
    cy.getNode(newNodeLabel).within(() => cy.contains('Stop node', { matchCase: false }).click());
  });

  it('Checks if user can see his Stopped Nodes', () => {
    cy.contains('Stopped').click();
    cy.get(tabPanel).should('have.length.at.least', 1);
  });

  it('Checks if user can run another Node', () => {
    cy.startNewNodeClick('Run new node').then(() => {
      cy.contains('Name your node');
      cy.contains('Choose network');
      cy.startNewNodeClick('Start node');
    });
  });
});
