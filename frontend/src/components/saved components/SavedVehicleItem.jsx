import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { MdDelete } from 'react-icons/md'
import { MapContext } from '../../App'

const SavedVehicleItem = ({vehicleItem, isEditing}) => {

    const navigate = useNavigate()
    const value = useContext(MapContext)
    const {savedVehicles, setSavedVehicles} = value

    return (
        <div 
        className={`flex-shrink-0 ml-3 flex justify-between items-center h-12 max-w-[14rem] rounded-[2rem] border-2 border-gray1 hover:bg-gray1 transition duration-200 cursor-pointer ${!isEditing ? 'px-4' : 'pr-2'}`}
        onClick={() => {
            if(!isEditing) navigate(`/search/bus/${vehicleItem.id}`)
        }}
        >
            {isEditing ?
            <>
            <div 
            className='h-12 w-12 mr-2 rounded-[2rem] hover:bg-gray2 transition duration-200 flex justify-center items-center'
            onClick={() => setSavedVehicles(savedVehicles.filter((e) => e.id!=vehicleItem.id))}
            >
                <MdDelete
                    className='h-6 w-6'
                />
            </div>
            <h1 className='font-semibold truncate pr-4'>{vehicleItem.license_plate}</h1>
            </>
            :
            <>
            <h1 className='font-semibold'>{vehicleItem.license_plate}</h1>
            {vehicleItem.nickname!='' &&
            <h1 className='font-semibold truncate pl-2'>{`(${vehicleItem.nickname})`}</h1>
            }
            </>
            }
        </div>
    )
}

export default SavedVehicleItem