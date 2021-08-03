/// <reference types="cypress" />

describe('Erigolem RPC Server tests', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000');
  });

  const addressLabel = 'Address';

  it('Checks if anchor link is correct', () => {
    cy.getNode(addressLabel).within(() =>
      cy.getHref().then((href) => cy.get('a').should('have.prop', 'innerText', href)),
    );
  });

  it('Checks if user can make request as unauthorized', () => {
    cy.getNode(addressLabel).within(() =>
      cy.getHref().then((href) =>
        cy
          .request({
            url: href,
            failOnStatusCode: false,
          })
          .its('status')
          .should('eq', 401),
      ),
    );
  });

  it('Checks if user can make request with wrong credentials', () => {
    cy.getNode(addressLabel).within(() =>
      cy.getHref().then((href) => {
        const url = `https://user:password@${href.split('//')[1]}`;

        cy.request({
          url,
          failOnStatusCode: false,
        })
          .its('status')
          .should('eq', 401);
      }),
    );
  });

  it('Checks if user can make request and authorize', function () {
    cy.getNode(addressLabel)
      .within(() => {
        cy.get('span[data-user]').invoke('attr', 'data-user').as('user');
        cy.get('span[data-password]').invoke('attr', 'data-password').as('password');
      })
      .within(() =>
        cy.getHref().then((href) => {
          const { user, password } = this;
          const url = `https://${user}:${password}@${href.split('//')[1]}`;

          cy.request({ url }).its('status').should('eq', 200);
        }),
      );
  });
});
