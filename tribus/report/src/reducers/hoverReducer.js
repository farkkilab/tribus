const initialState = {
    celltype:"",
    marker:""
}

const hoverReducer = (state=initialState, action) => {
    switch(action.type) {
        case 'SET_HOVER':
            return {
                celltype:action.celltype,
                marker:action.marker
            }
        default:
            return state
    }
}

export const setHover = (ctype, marker) =>{
    return{
        type: "SET_HOVER",
        celltype:ctype,
        marker:marker
    }
}

export default hoverReducer