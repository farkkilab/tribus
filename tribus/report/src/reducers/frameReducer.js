import { v4 as uuidv4 } from 'uuid';
//import exdata from '../data/example.js'
//import BarPlot from '../components/plots/BarPlot'
import HeatmapPlot from '../components/plots/HeatmapPlot'
import PiePlot from '../components/plots/PiePlot'
import ScatterPlot from '../components/plots/ScatterPlot';

//const examplePlot =  BarPlot({data:exdata})

const frameReducer = (state = [], action) => {
    switch(action.type) {
      case 'NEW_FRAME':
        return [...state, action.data]
      case 'REMOVE_FRAME':
        var id = action.data.id
        return state.filter(frame => frame.id !== id)
      case 'ADD_DATA':
        // eslint-disable-next-line no-redeclare
        var id = action.data.id
        var frames = state.slice()
        var plot_func;
        switch(action.data.plot_type) {
          case "heatmapdata":
            plot_func = HeatmapPlot
            break
          case "piechartdata":
            plot_func = PiePlot
            break
          case "umapdata":
            plot_func = ScatterPlot
            break
          default:
            plot_func = console.log
            break
        }
        console.log(action.data)
        frames.splice(frames.findIndex(f=>f.id===id),1,{
          id:id,
          layout: {
            x:0,
            y:0,
            w:30,
            h:30,
          },
          plot:{
            plot:plot_func({data:action.data.data}),
            id:id
          }
        })
        console.log(frames)
        return frames
      default:
        return state
    }
  }

export const createFrame = (plot=[]) => {
  const id = uuidv4()
  return {
    type: 'NEW_FRAME',
    data: {
      id:id,
      layout: {
        x:0,
        y:0,
        w:30,
        h:30,
      },
      plot:{
        plot:plot,
        id:id
      }
    }
  }
}

export const removeFrame = (id) => {
  return {
    type: 'REMOVE_FRAME',
    data: {id}
  }
}

export const addDataToPlot = (id,data,sample_name,plot_type) => {
  return {
    type: 'ADD_DATA',
    data: {"id":id,
      "data":data,
      "plot_type":plot_type,
      "sample_name":sample_name}
  }
}


export default frameReducer