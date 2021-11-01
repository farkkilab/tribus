
const initialState = {
    open:false,
    data:{
    }
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


export default setupReducer