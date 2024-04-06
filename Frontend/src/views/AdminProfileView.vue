<template>
    <div>
      <NavBarProfile :title="title"></NavBarProfile>
      <div class="container mt-5">
        <div class="row">
          <div class="mx-auto">
            <div class="card">
              <div class="card-header bg-primary text-white">
                Admin Profile
              </div>
              <div class="card-body d-flex justify-content-between align-items-center">
                <!-- Add profile photo display -->
                <div class="col-4">
                  <div class="card">
                    <div class="card-body text-center">
                      <div class="center">
                        <img :src="profilePhotoUrl" class="profile-photo" alt="Profile Photo">
                      </div>
                      <!-- Add profile photo update -->
                      <div class="form-group">
                        <label for="profilePhoto">Update Photo</label>
                        <input type="file" class="form-control-file" id="profilePhoto" @change="updateProfilePhoto">
                      </div>
                    </div>
                  </div>
                </div>
                <!-- Add Google chat notifications -->
                <div class="col-8 profile-form" style="border: darkslategrey">
                  <div class="card">
                    <div class="card-body">
                      <div class="form-group">
                        <label for="firstName">First Name</label>
                        <input type="text" class="form-control" id="firstName" v-model="firstName">
                      </div>
                      <div class="form-group">
                        <label for="lastName">Last Name</label>
                        <input type="text" class="form-control" id="lastName" v-model="lastName">
                      </div>
                      <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" class="form-control" id="email" v-model="email">
                      </div>
                      <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" class="form-control" id="password" v-model="password">
                      </div>
                    </div>
                  </div>
                  <br>
                  <div class="card">
                    <div class="card-body">
                      <div class="form-group">
                        <h4 class="card-title">Google Chat Notifications</h4>
                        
                        <input type="checkbox" id="highprioritynotifications" v-model="ticketNotifications">
                        <label for="highprioritynotifications">High Priority Notifications</label><br>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <button class="btn btn-primary" @click="updateProfile">Update Profile</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import NavBarProfile from "@/components/NavBarProfile.vue";
  
  export default {
    name: "AdminProfileView",
    components: {
      NavBarProfile
    },
    data() {
      return {
        firstName: "", // Initialize with user's first name
        lastName: "", // Initialize with user's last name
        email: "", // Initialize with user's email
        password: "", // Initialize with user's password
        profilePhoto: null, // Initialize with user's profile photo
        profilePhotoUrl: require("@/assets/default-profile-photo.jpeg"), // Default profile photo
        highprioritynotifications: false, // Initialize with high priority notifications preference
      };
    },
    created() {
      // Fetch user data from API or local storage and update data properties
      this.firstName = localStorage.getItem("user_firstName");
      this.lastName = localStorage.getItem("user_lastName");
      this.email = localStorage.getItem("user_email");
      // Fetch other profile data as needed
    },
    methods: {
      updateProfilePhoto(event) {
        // Handle updating profile photo
        this.profilePhoto = event.target.files[0];
        // Update the profile photo preview
        if (this.profilePhoto) {
          this.profilePhotoUrl = URL.createObjectURL(this.profilePhoto);
        }
      },
      updateProfile() {
        // Handle updating profile details
        // Example: Send updated profile data to backend API
        console.log("Updated profile details:", {
          firstName: this.firstName,
          lastName: this.lastName,
          email: this.email,
          password: this.password,
          profilePhoto: this.profilePhoto,
          highprioritynotifications: this.highprioritynotifications,
        });
      }
    }
  };
  </script>
  
  <style scoped>
  .card {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  
  .card-header {
    background-color: #6B62FF;
  }
  
  input[type="text"],
  input[type="email"],
  input[type="password"] {
    border-radius: 0;
  }
  
  .profile-photo {
    width: 150px; /* Adjust the size as needed */
    height: 150px; /* Adjust the size as needed */
    border-radius: 50%;
    object-fit: cover;
  }
  
  .profile-form {
    flex: 1; /* Take remaining space */
    padding-left: 20px; /* Adjust spacing */
  }
  </style>
  