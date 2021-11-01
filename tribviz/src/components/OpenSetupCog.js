import React from 'react'
import { useDispatch } from 'react-redux'
import cog from '../icons/cog.png'
import { openSetup } from '../reducers/setupReducer'

const OpenSetupCog = ({id}) => {
    const dispatch = useDispatch()

    const oSetup = () => {
        dispatch(openSetup(id))
    }

    return(
        <div className="openSetupCog" onMouseDown={oSetup}>
            <img src={cog} style={{width:"inherit", height:"inherit"}}
             alt="Open options"/>
        </div>
    )

}
export default OpenSetupCog
