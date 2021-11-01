import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { closeSetup } from '../reducers/setupReducer'
import { addDataToPlot } from '../reducers/frameReducer'
import PlotFrame from './PlotFrame'

const FrameSetup = () => {
    const dispatch = useDispatch()
    const setup = useSelector(state =>state.setup)
    const frames = useSelector(state =>state.frames)

    const cSetup = (event) => {
        event.preventDefault()
        dispatch(closeSetup())
    }
    const addData = (event) => {
        event.preventDefault()
        dispatch(addDataToPlot(setup.data.id))
    }
    var classname = "setup"
    if(!setup.open) {
        classname = "setup closedSetup"
    }
    return(
        <div className={classname}>
            {setup.open?
                <div>
                    <h2>Preview</h2>
                    <p>{setup.data.id}</p>
                    <div className="preview">
                        <PlotFrame  plot={frames.filter(f=>f.id===setup.data.id)[0].plot} />
                    </div>
                    <button onClick={addData}>Add data</button>
                    <button onClick={cSetup}>Close setup</button>
                </div>
            :null}
        </div>
    )

}
export default FrameSetup