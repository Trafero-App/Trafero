import {IoIosArrowBack} from 'react-icons/io'
import { ClipLoader } from 'react-spinners'
import NearbyRouteItem from './NearbyRouteItem'
import { useContext } from 'react'
import { MapContext } from '../../App'

const NearbyRoutesResults = ({
    areNearbyRoutesLoading, setNearbyRoutesLoading,
    nearbyRoutes, previewedIds,
    setPreviewedIds
}) => {
    const value = useContext(MapContext)
    const {setChosenBusIds, chosenBusIds} = value
    return (
        <div className='pointer-events-auto w-full max-w-96 rounded-xl bg-white shadow-md'>
            <div 
            className='text-gray4 flex items-center h-12 border-b-2 border-gray1'
            style={{cursor: 'pointer'}}
            onClick={() => {
                setChosenBusIds(null)
                setNearbyRoutesLoading(false)
            }}
            >
                <IoIosArrowBack
                className='mx-2 h-8 w-8 text-gray4'
                />
                <h1 className='text-[18px] lg:text-[16px]'>Back to Search</h1>
            </div>
            {areNearbyRoutesLoading && !nearbyRoutes ?
            <div className='pointer-events-auto flex justify-center items-center my-3'>
                <ClipLoader size='29px' color='#C8C8C8'/>
            </div> 
            :
            nearbyRoutes.length==0 ?
            //there are no results
            <div className='pointer-events-auto flex justify-center items-center my-3'>
                <h1 className='text-gray4'>There are no nearby routes</h1>
            </div> 
            :
            <div className={`my-3 ${nearbyRoutes.length>=3 && 'scrollable h-36'}`}>
            {nearbyRoutes.map((element,index) => 
            <NearbyRouteItem 
            key={index} 
            routeData={element}
            previewedIds={previewedIds}
            setPreviewedIds={setPreviewedIds}
            />)}
            </div>
            }   
        </div>
    )
}

export default NearbyRoutesResults