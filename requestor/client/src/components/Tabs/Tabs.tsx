import React from 'react';
import { Col, Row } from 'react-grid-system';
import { Tab, TabList, TabPanel } from 'react-tabs';
import { TabProps, TabsProps } from './types';
import { StyledTabs } from './styles';

const tabs = [
  { id: 0, name: 'Active' },
  { id: 1, name: 'Stopped' },
];

const Tabs = ({ children, count }: TabsProps) => (
  <StyledTabs defaultIndex={0}>
    <Row nogutter>
      <Col xs={12}>
        <TabList>
          {tabs.map((tab: TabProps) => (
            <Tab key={tab.id}>
              {tab.name} ({tab.name === tabs[0].name ? count.active : count.stopped})
            </Tab>
          ))}
        </TabList>
      </Col>
    </Row>
    {children}
  </StyledTabs>
);

export default Tabs;
export { TabPanel };
