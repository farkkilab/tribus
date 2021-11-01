import {React, memo} from 'react'


export const PlotFrame = ({plot}) => {
  if (plot.plot.length === 0) { // check for []
    return(
      <div className="emptyplot">
        <span className="emptytext">The plot is empty</span>
      </div>
    )
  } else {
    return(
      <div className="plot">
        {plot.plot}
      </div>)
  }
  }


export default memo(PlotFrame);