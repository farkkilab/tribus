import React from 'react'
import { useDispatch } from 'react-redux'
import { removeFrame } from '../reducers/frameReducer'

const RemoveFrameX = ({id}) => {
    const dispatch = useDispatch()

    const remFrame = () => {
        dispatch(removeFrame(id))
    }

    return(
        <span className="removerX" onMouseDown={remFrame}>X</span>
    )

}
export default RemoveFrameX
