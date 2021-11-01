import './App.css';
import '../node_modules/react-grid-layout/css/styles.css'
import '../node_modules/react-resizable/css/styles.css'
import PlotCanvas from './components/PlotCanvas'
import AddFrameButton from './components/AddFrameButton'
import FrameSetup from './components/FrameSetup';

const App = () => {
  //const [frames, setFrames] = useState([
  //   { plot: BarPlot({data:exdata}), id:"a" },
  //   { plot: 'Drag me too', id:"b" }])
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
