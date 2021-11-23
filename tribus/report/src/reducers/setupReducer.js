
const initialState = {
    open:false,
    data:{
    },
    selected_sample:"",
    selected_plot_type:""
}

const setupReducer = (state = initialState, action) => {
    switch(action.type) {
      case 'OPEN_SETUP':
          console.log("Opening setup")
        return {
            open:true,
            data:action.data
        }
      case 'CLOSE_SETUP':
        return {
            open:false
        }
      case 'SELECT_SAMPLE':
        return {
          open:state.open,
          data:state.data,
          selected_sample:action.selected_sample
        }
      case 'SELECT_PLOT_TYPE':
        return{
          open:state.open,
          data:state.data,
          selected_sample:state.selected_sample,
          selected_plot_type:action.selected_plot_type
        }
      default:
      return state
    }
}

export const openSetup = (plotID) => {
  return {
    type: 'OPEN_SETUP',
    data: {
        id:plotID,
    }
  }
}

export const closeSetup = () => {
  return {
    type: 'CLOSE_SETUP',
    data: {}
  }
}

export const selectSample = (sample) => {
  return {
    type: 'SELECT_SAMPLE',
    selected_sample: sample
  }
}

export const selectPlotType = (plot_type) => {
  return {
    type: 'SELECT_PLOT_TYPE',
    selected_plot_type: plot_type
  }
}


export default setupReducer