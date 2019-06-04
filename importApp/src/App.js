/* eslint-disable no-unused-vars */
import React from 'react';
import {connect} from 'react-redux'

import DataPrep from './containers/DataPrep';
import DataModification from './containers/DataModification';
import FileUpload from './containers/FileUpload';
import SchemaValidation from './containers/SchemaValidation';
import Layout from './containers/Layout';
import styles from 'design-workshop/themes/default/style.css';
import './App.css';

import { 
  setStep
} from './redux/modules/ui';

const App = ({
  steps,
  selectedStep,
  repoData,
  //actions
  setStep
}) => {
  const renderChildren = () => {
    switch(selectedStep.id) {
      case '0':
      default:
        return <FileUpload />;
      case '1':
        return <SchemaValidation />;
      case '2':
        return <DataModification />;
    }
  }
  
  return (
    <div className="App">
      <DataPrep />
      { repoData.descriptor &&
        <Layout 
          steps={steps}
          selectedStep={selectedStep}
          onSetStep={setStep}>
          {renderChildren()}
        </Layout>
      }
    </div>
  );
}


const mapStateToProps = state => ({
  steps: state.ui.steps,
  selectedStep: state.ui.selectedStep,
  repoData: state.repoData
 })
 
 export default connect(mapStateToProps, {
  setStep
 })(App);
