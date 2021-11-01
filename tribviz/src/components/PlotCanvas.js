import { Responsive, WidthProvider } from 'react-grid-layout';
import { createRef } from "react";
import { useSelector } from 'react-redux'
import { DraggableFrame } from './DraggableFrame';
const ResponsiveGridLayout = WidthProvider(Responsive);
//var _ = require('lodash');

export const PlotCanvas = () => {
  const frames = useSelector(state => state.frames)
  const layout = frames.map(oneFrame => oneFrame.layout)
  
  const childFrames = frames.map(oneframe => <DraggableFrame ref={createRef()} frame={oneframe} key={oneframe.id} />);
  return(<div className="canvas">
    <ResponsiveGridLayout className="layout" layout={layout} draggableHandle=".drag-handle"
      breakpoints={{lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0}}
      cols={{lg: 12, md: 10, sm: 6, xs: 4, xxs: 2}}>
        {childFrames}
    </ResponsiveGridLayout>
  </div>)

}

export default PlotCanvas