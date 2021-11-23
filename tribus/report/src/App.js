import './App.css';
import '../node_modules/react-grid-layout/css/styles.css'
import '../node_modules/react-resizable/css/styles.css'
import PlotCanvas from './components/PlotCanvas'
import AddFrameButton from './components/AddFrameButton'
import FrameSetup from './components/FrameSetup';


const App = () => {
  return (
    <div className="App">
      <AddFrameButton />
        <div className="botApp">
          <FrameSetup />
          <PlotCanvas />
          
        </div>

    </div>
  );
}

export default App;
