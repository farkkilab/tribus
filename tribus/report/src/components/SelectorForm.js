import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { selectPlotType, selectSample } from '../reducers/setupReducer'

const SelectorForm = () => {
    const dispatch = useDispatch()
    const setup = useSelector(state =>state.setup)
    const data = useSelector(state =>state.data)


    const changeSelectSample = (event) => {
        dispatch(selectSample(event.target.value))
    }

    const changeSelectPT = (event) => {
        dispatch(selectPlotType(event.target.value))
    }

    return(
        <form>
            <label>
                Select the data you wish to plot: 
            <select value={setup.selected_sample ||''} onChange={changeSelectSample}>
                <option value=''></option>
                {data.sample_names.map(sn => <option value={sn} key={sn}>{sn}</option>)}
            </select>
            </label>
            
            {setup.selected_sample?<div>
            <br />
            <label>
                Select the type of plot: 
            <select value={setup.selected_plot_type ||''} onChange={changeSelectPT}>
                <option value=''></option>
                {data.plot_types[setup.selected_sample].map(pt => <option value={pt} key={pt}>{pt}</option>)}
            </select>
            </label></div>:null}
            
        </form>
    )
}

export default SelectorForm