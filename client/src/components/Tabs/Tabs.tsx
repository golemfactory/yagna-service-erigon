import React from 'react';
import { Tab, TabList, TabPanel } from 'react-tabs';
import { TabProps, TabsProps } from './types';
import { StyledTabs } from './styles';

const tabs = [
  { id: 0, name: 'Active' },
  { id: 1, name: 'Stopped' },
];

const Tabs = ({ children, count, button }: TabsProps) => (
  <StyledTabs defaultIndex={0}>
    <TabList>
      {button}
      {tabs.map((tab: TabProps) => (
        <Tab key={tab.id}>
          {tab.name} ({tab.name === tabs[0].name ? count.active : count.stopped})
        </Tab>
      ))}
    </TabList>
    {children}
  </StyledTabs>
);

export default Tabs;
export { TabPanel };
