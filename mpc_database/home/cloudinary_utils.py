import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

def delete_cloudinary_file(name, default_resource_type="image"):
    if not name:
        return
    if ":" in name:
        resource_type, public_id = name.split(":", 1)
    else:
        public_id = name
        resource_type = default_resource_type
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        logger.warning(f"Failed to delete Cloudinary asset '{public_id}': {e}")