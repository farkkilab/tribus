import { ResponsiveHeatMapCanvas } from '@nivo/heatmap'
import { useDispatch, useSelector  } from 'react-redux'
import { setHover } from '../../reducers/hoverReducer'

// make sure parent container have a defined height when using
// responsive component, otherwise height will be 0 and
// no chart will be rendered.
const HeatmapPlot = ({ data }) => {
    const allkeys = Object.keys(data[0])
    // Don't include the variances or the celltype as rows
    const keys = allkeys.filter(k => !(k.includes("_")|k==="celltype"))


    return(<ResponsiveHeatMapCanvas
        data={data}
        keys={keys}
        indexBy="celltype"
        margin={{ top: 100, right: 60, bottom: 60, left: 60 }}
        forceSquare={true}
        colors="RdYlBu"
        axisTop={{ orient: 'top', tickSize: 5, tickPadding: 5, tickRotation: -90, legend: '', legendOffset: 36 }}
        axisRight={null}
        axisBottom={null}
        axisLeft={{
            orient: 'left',
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'celltype',
            legendPosition: 'middle',
            legendOffset: -40
        }}
        cellOpacity={1}
        cellBorderColor={{ from: 'color', modifiers: [ [ 'darker', 0.4 ] ] }}
        label={(datum, key) =>
            `${Number(datum[key]).toFixed(2)}`
        }
        tooltip={({ xKey, yKey, value, color }) => (
            <strong>
                {xKey} for {yKey}: mean={Number(value).toFixed(2)}, var={Number(data.filter(su => su["celltype"]===yKey)[0][xKey+"_var"]).toFixed(3)}
            </strong>
        )}
        labelTextColor={{ from: 'color', modifiers: [ [ 'darker', 1.8 ] ] }}
        defs={[
            {
                id: 'lines',
                type: 'patternLines',
                background: 'inherit',
                color: 'rgba(0, 0, 0, 0.1)',
                rotation: -45,
                lineWidth: 4,
                spacing: 7
            }
        ]}
        fill={[ { id: 'lines' } ]}
        animate={true}
        motionConfig="wobbly"
        motionStiffness={80}
        motionDamping={9}
        hoverTarget="rowColumn"
        cellHoverOthersOpacity={0.25}
    />)
    }

export default HeatmapPlot